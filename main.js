const puppeteer = require('puppeteer')
const prompts = require('prompts')
const signale = require('signale')
const fs = require('fs')

const $loggedMenu =
  '#root > div > div.height-holder-mobile > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > div > div > div.actions-container.actions-container_logged'

let browser
let page

const login = async () => {
  await page.click(
    '#root > div > div.height-holder-mobile > div > div > div > div > div.main-content > div > div > div.container.exchange-lots-list-container > div > div.col-xs-12.col-sm-5 > div > span > a.btn.btn-black.hidden-xs'
  )
  const loginLink = await page.waitForSelector(
    '#exchangeAuthRequiredPopup > div > div > div > div > div.popup-content > div > p:nth-child(1) > a'
  )
  await loginLink.click()
  const phoneField = await page.waitForSelector('#keycloakAuth\\.phone')
  await phoneField.focus()

  await phoneField.type('9044979272')
  await page.click(
    '#keycloakLoginModal > div > div > div > div > div.popup-content > div > div > div > form > div.keycloak-login-form__container-buttons.btns-box.left.center-xs > button'
  )

  const firstSymbolField = await page.waitForSelector('#codeSymbolField1_0')

  const response1 = await prompts({
    type: 'text',
    name: 'code',
    message: 'phone confirmation code:'
  })

  await firstSymbolField.type(response1.code)

  await page.waitForSelector(
    '#root > div > div.height-holder-mobile > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > div > div > div.actions-container.actions-container_logged'
  )

  const cookies = await page.cookies()
  await fs.promises.writeFile(
    './cookies.json',
    JSON.stringify(cookies, null, 2)
  )

  signale.info('Cookies saved to `cookies.json` for future reuse.')
}

const goHomePage = async () => {
  if (fs.existsSync('./cookies.json')) {
    signale.success('`cookies.json` found!')
    const cookiesString = await fs.promises.readFile('./cookies.json')
    const cookies = JSON.parse(cookiesString)
    await page.setCookie(...cookies)
  } else signale.warn('`cookies.json` not found')

  await page.goto('https://tyumen.tele2.ru/stock-exchange/internet')

  return (await page.$($loggedMenu)) !== null
}

const sell = async batches => {
  for (const batch of batches) {
    await page.goto('https://tyumen.tele2.ru/stock-exchange/internet', {
      waitUntil: ['domcontentloaded', 'networkidle0']
    })
    await page.click(
      '#root > div > div.height-holder-mobile > div > div > div > div > div.main-content > div > div > div.container.exchange-lots-list-container > div > div.col-xs-12.col-sm-5 > div > span > a.btn.btn-black.hidden-xs'
    )
    const link = await page.waitForSelector(
      '#exchangeNewLotPopup > div > div > div > div > div.popup-content > div > div.lot-setup__manual-input > a'
    )
    await link.click()
    const gigField = await page.waitForSelector(
      '#exchangeNewLotPopup > div > div > div > div > div.popup-content > div > div.lot-setup__field > div > div.label-holder.counter-field-holder > input'
    )
    await gigField.focus()
    await page.keyboard.press('Backspace')
    await gigField.type(batch.toString())
    await page.click(
      '#exchangeNewLotPopup > div > div > div > div > div.popup-content > div > div.btns-box > a.btn.btn-black'
    )
  }
}

const sellPart = async () => {
  await page.hover(
    '#root > div > div.height-holder-mobile > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > div > div > div.actions-container.actions-container_logged > div:nth-child(1) > div'
  )

  const left = await page.$(
    '#root > div > div.height-holder-mobile > div > div > div > div > div:nth-child(1) > div > div > div > div:nth-child(2) > div > div > div > div.actions-container.actions-container_logged > div:nth-child(1) > div > div > div.action-popup > div > div > div > div.profile-popup_left > div.profile-popup_rests.profile-popup_block > div > div:nth-child(3) > span > span'
  )
  const count = await page.evaluate(
    element => +element.textContent.split(',')[0],
    left
  )

  signale.info(`You have ${count}`)

  let batches

  while (true) {
    const list = await prompts({
      type: 'list',
      name: 'value',
      message: 'Bathes (ex: 13 25 11)',
      initial: '',
      separator: ' '
    })

    batches = list.value.map(v => +v)
    const total = batches.reduce((t, c) => t + c)
    if (total > count)
      signale.error(`You dont have ${total}. Its only ${count}`)
    else break
  }

  await sell(batches)
}

const returnPart = async () => {
  while (true) {
    await page.goto('https://tyumen.tele2.ru/stock-exchange/my', {
      waitUntil: ['domcontentloaded', 'networkidle0']
    })
    const myLot = await page.$(
      '#root > div > div.height-holder-mobile > div > div > div > div > div.main-content > div > div > div.container > div > div.col-xs-12.col-sm-7 > div > div.exchange-block__lots-group-block.my-active-lots > div.my-active-lots__list > div:nth-child(1)'
    )
    if (myLot !== null) {
      await page.click(
        '#root > div > div.height-holder-mobile > div > div > div > div > div.main-content > div > div > div.container > div > div.col-xs-12.col-sm-7 > div > div.exchange-block__lots-group-block.my-active-lots > div.my-active-lots__list > div:nth-child(1) > div.my-lot-item__edit-lot > a > i'
      )
      const returnBtn = await page.waitForSelector(
        '#exchangeEditLotPopup > div > div > div > div > div.popup-content > div > div.btns-box > a:nth-child(2)'
      )
      await returnBtn.click()
      const confirmBtn = await page.waitForSelector(
        '#requestExecutorPopup > div > div > div > div > div.popup-content > div > div.btns-box.left.center-xs > span:nth-child(1) > a'
      )
      await confirmBtn.click()
    } else break
  }
}

;(async () => {
  browser = await puppeteer.launch({
    defaultViewport: { width: 1920, height: 1080 }
  })

  page = await browser.newPage()
  const logged = await goHomePage()

  if (logged) {
    signale.success('Cookies applied! You are signed in!')
  } else {
    signale.error('Cookies not applied.')
    await login()
  }

  await page.reload({ waitUntil: ['domcontentloaded', 'networkidle0'] })

  const choice = await prompts({
    type: 'select',
    name: 'value',
    message: 'Pick an action',
    choices: [
      { title: 'Sell', description: 'Sell your gigs', value: 'sell' },
      {
        title: 'Return',
        description: 'Return all gigs from market',
        value: 'return'
      }
    ],
    initial: 1
  })

  if (choice.value === 'sell') await sellPart()
  else if (choice.value === 'return') await returnPart()

  await browser.close()
  signale.complete('Closed and terminated.')
})()
